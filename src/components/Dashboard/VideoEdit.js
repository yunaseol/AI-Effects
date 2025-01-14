import React, { useCallback, useState } from 'react'
import styled from 'styled-components';

import Preview from "./Preview"
import { getSrcUrl } from "../../variables"

import { blurVideo, getPeople, mergeVideo } from "../../utils/api"

import split from '../../static/icons/columns-solid.svg';
import mergeIcon from '../../static/icons/call_merge-24px.svg'
import tongueSlipFix from '../../static/icons/wrench-solid.svg'
import caption from '../../static/icons/closed-captioning-regular.svg'

import Spinner from "../Spinner"

const Wrapper = styled.div`
	width: 100%;
	height: 100%;
	display: flex;
	flex-direction: column;
	justify-content: center;
`

const Menus = styled.div`
	width: 100%;
	justify-self: flex-end;
	display: flex;
	border-top: 1px solid rgb(8,8,8);
	height: 60px;
	padding: 6px 24px;
	
	.menu-item {
		box-sizing: content-box;
		height: 100%;
		width: auto;
		&:hover {
			cursor: pointer;
			border: 1px solid #e5e5e5;
		}
		&.loading {
			opacity: 0.3;
			border: 1px solid #e5e5e5;
		}
	}
	img + img {
		margin-left: 30px;
	}
`

const Blur = (props) => {
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);

	const process = props.blurSrc ? props.toggle : async () => {
		setLoading(true);
		try {
			const result = await blurVideo (props.fileName, props.knowns || []);
			props.setResolved (result.data);
		} catch (e) {
			setError(e);
		}
		setLoading(false);
	};

	return <>{loading && <Spinner />}<img
							onClick={process}
							src='http://www.jigzone.com/p/jz/jzM/Mozaic_Face_5310.jpg'
							className={`menu-item face-blur ${loading ? 'loading' : ''}`}
						/></>
}

const AddVideo = (props) => {
	return <img className={'menu-item'} src={split} onClick={() => {
		props.tabAction({
			type: 'split'
		})
	}}/>
}

const MergeVideo = (props) => {
	const { tabs, name } = props
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);

	const process = props.blurSrc ? props.toggle : async () => {
		setLoading(true);
		try {
			const index = tabs.findIndex(x => x.name === name);
			const result = await mergeVideo(name, tabs[index+1].name);
			props.setResolved (result.data);
			props.tabAction({
				type: 'merged'
			})
		} catch (e) {
			setError(e);
		}
		setLoading(false);
	};

	return <>
		{loading && <Spinner />}
			<img
			className={`menu-item ${loading ? 'loading' : ''}`}
			src={mergeIcon} onClick={process} />
		</>
}

const VideoEdit = (props) => {
	console.log('video edit', props);
	const { fileName } = props;
	const defSrc = `/uploads/${fileName}`

	const [src, setSrc] = useState (defSrc)
	const [blurSrc, setBlurSrc] = useState ('');
	const [mergeSrc, setMergeSrc] = useState ('');

	const toggle = useCallback (() => {
		console.log(src)
		if (src != blurSrc) setSrc (blurSrc)
		else setSrc (defSrc)
	}, [src, blurSrc])

	const toggleMerge = useCallback (() => {
		if (src != mergeSrc) setSrc (mergeSrc)
		else setSrc (defSrc)
	}, [src, mergeSrc])

	return (
		<Wrapper>
			<Preview previewUrl={getSrcUrl(src)} />
			<Menus>
				<Blur fileName={fileName} setResolved={setBlurSrc} blurSrc={blurSrc} toggle={toggle} knowns={props.knowns}/>
				<img className={`menu-item`} src={tongueSlipFix} />
				<img className={`menu-item`} src={caption} />
				{props.merged || <AddVideo {...props} />}
				{(props.merged || mergeSrc) && <MergeVideo {...props} toggle={toggleMerge} mergeSrc={mergeSrc} setResolved={setMergeSrc} />}
			</Menus>
		</Wrapper>
	)
}

export default VideoEdit;
